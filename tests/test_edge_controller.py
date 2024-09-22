# app/tests/test_edge_controller.py

"""
Test Suite for EdgeController

This module contains comprehensive tests for the EdgeController class, focusing on
CRUD operations, partial data handling, and various edge cases. It utilizes pytest
and unittest.mock for structuring and mocking dependencies respectively.

Functionalities Tested:
1. Edge Creation:
   - Creating an edge with full data
   - Creating an edge with minimal required data
   - Handling edge creation failures

2. Edge Retrieval:
   - Getting an edge by ID
   - Handling retrieval of non-existent edges

3. Edge Update:
   - Updating an edge with full data
   - Updating an edge with partial data
   - Handling update of non-existent edges

4. Edge Deletion:
   - Deleting an existing edge
   - Handling deletion of non-existent edges

5. Edge Listing:
   - Retrieving a list of all edges
   - Handling empty edge lists

6. Edge Verification:
   - Verifying that an edge can connect two blocks
   - Verifying that an edge cannot connect due to existing edges
   - Verifying that an edge cannot connect due to incompatible block types
   - Verifying that an edge cannot connect due to potential cycle creation

7. Error Handling:
   - Proper HTTP exceptions for various error scenarios
   - Validation of error messages and status codes

8. Audit Logging:
   - Verification of audit log creation for all CRUD operations

9. Input Validation:
   - Handling of invalid input data for create and update operations

10. Service Integration:
    - Correct interaction between EdgeController and EdgeService
    - Proper use of mocked EdgeService methods

11. Response Formatting:
    - Correct schema usage for request and response data

12. Edge-specific Business Logic:
    - Validation of edge type constraints
    - Handling of edge metadata

This test suite ensures the robustness and reliability of the EdgeController,
covering both happy paths and edge cases to maintain the integrity of edge-related
operations within the application.
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4, UUID
from typing import Optional, Dict, Any, List
from datetime import datetime

# ... (rest of the imports and test code)

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4, UUID
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import HTTPException, status

# Import the controller and schemas
from app.controllers.edge_controller import EdgeController
from app.schemas import (
    EdgeCreateSchema,
    EdgeUpdateSchema,
    EdgeResponseSchema,
    EdgeVerificationRequestSchema,
    EdgeVerificationResponseSchema
)

from app.models import EdgeTypeEnum

# -------------------
# Fixtures
# -------------------

@pytest.fixture
def mock_edge_service():
    """
    Fixture to mock the EdgeService used by EdgeController.
    """
    with patch('app.controllers.edge_controller.EdgeService') as MockService:
        mock_service_instance = MockService.return_value
        yield mock_service_instance

@pytest.fixture
def mock_audit_service():
    """
    Fixture to mock the AuditService used by EdgeController.
    """
    with patch('app.controllers.edge_controller.AuditService') as MockAuditService:
        mock_audit_instance = MockAuditService.return_value
        yield mock_audit_instance

@pytest.fixture
def edge_controller_instance(mock_edge_service, mock_audit_service):
    """
    Fixture to instantiate the EdgeController with mocked services.
    """
    controller = EdgeController()
    controller.edge_service = mock_edge_service
    controller.audit_service = mock_audit_service
    controller.logger = MagicMock()  # Mock the logger to prevent actual logging during tests
    return controller

# -------------------
# Sample Data
# -------------------

def generate_uuid() -> UUID:
    return uuid4()

@pytest.fixture
def sample_edge_create_full():
    """
    Sample EdgeCreateSchema with all fields populated.
    """
    return EdgeCreateSchema(
        name="FullEdge123",
        edge_type=EdgeTypeEnum.primary,
        description="A fully detailed edge.",
        created_by=uuid4()
    )

@pytest.fixture
def sample_edge_response(sample_edge_create_full):
    """
    Sample EdgeResponseSchema with all fields populated.
    Ensures that 'created_by' matches the one in 'sample_edge_create_full'.
    """
    return EdgeResponseSchema(
        edge_id=uuid4(),
        name=sample_edge_create_full.name,
        edge_type=sample_edge_create_full.edge_type,
        description=sample_edge_create_full.description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by=sample_edge_create_full.created_by
    )

@pytest.fixture
def sample_edge_create_partial():
    """
    Sample EdgeCreateSchema with only mandatory fields.
    """
    return EdgeCreateSchema(
        name="PartialEdge456",
        edge_type=EdgeTypeEnum.secondary
        # description and created_by are omitted
    )

@pytest.fixture
def sample_edge_update_full():
    """
    Sample EdgeUpdateSchema with all fields populated.
    """
    return EdgeUpdateSchema(
        name="UpdatedEdge789",
        edge_type=EdgeTypeEnum.tertiary,
        description="An updated edge description.",
        updated_by=generate_uuid()  # Added updated_by field
    )

@pytest.fixture
def sample_edge_update_partial():
    """
    Sample EdgeUpdateSchema with only some fields populated.
    """
    return EdgeUpdateSchema(
        description="Partially updated description.",
        updated_by=generate_uuid()  # Added updated_by field
        # name and edge_type are omitted
    )

# -------------------
# Test Cases
# -------------------

class TestEdgeController:
    """
    Test suite for the EdgeController class.
    """

    # -------------------
    # Create Edge Tests
    # -------------------

    def test_create_edge_with_full_data(self, edge_controller_instance, sample_edge_create_full, sample_edge_response):
        """
        Test creating an edge with complete data.
        """
        # Mock the service to return the sample_edge_response
        edge_controller_instance.edge_service.create_edge.return_value = sample_edge_response

        # Invoke the controller's create_edge method
        result = edge_controller_instance.create_edge(sample_edge_create_full)

        # Assertions
        assert isinstance(result, EdgeResponseSchema)
        assert result.name == sample_edge_create_full.name  # "FullEdge123"
        assert result.edge_type == sample_edge_create_full.edge_type
        assert result.description == sample_edge_create_full.description
        assert result.created_by == sample_edge_create_full.created_by

        # Ensure that audit_log was created
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()

    def test_create_edge_with_partial_data(self, edge_controller_instance, sample_edge_create_partial, sample_edge_response):
        """
        Test creating an edge with partial data (missing optional fields).
        """
        # Adjust the sample_edge_response to reflect partial data
        partial_response = EdgeResponseSchema(
            edge_id=sample_edge_response.edge_id,
            name=sample_edge_create_partial.name,
            edge_type=sample_edge_create_partial.edge_type,
            description=None,  # Description was omitted
            created_at=sample_edge_response.created_at,
            updated_at=sample_edge_response.updated_at,
            created_by=None  # created_by was omitted
        )

        edge_controller_instance.edge_service.create_edge.return_value = partial_response

        # Invoke the controller's create_edge method
        result = edge_controller_instance.create_edge(sample_edge_create_partial)

        # Assertions
        assert isinstance(result, EdgeResponseSchema)
        assert result.name == sample_edge_create_partial.name
        assert result.edge_type == sample_edge_create_partial.edge_type
        assert result.description is None
        assert result.created_by is None

        # Ensure that audit_log was created
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()

    def test_create_edge_with_invalid_edge_type(self, edge_controller_instance, sample_edge_create_full):
        """
        Test creating an edge with an invalid edge_type, expecting failure.
        """
        # Configure the service to return None, indicating failure
        edge_controller_instance.edge_service.create_edge.return_value = None

        # Invoke the controller's create_edge method and expect an HTTPException
        with pytest.raises(HTTPException) as exc_info:
            edge_controller_instance.create_edge(sample_edge_create_full)

        # Assertions
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "Edge creation failed due to invalid data."

        # Ensure that audit_log was not created
        edge_controller_instance.audit_service.create_audit_log.assert_not_called()

    # -------------------
    # Retrieve Edge Tests
    # -------------------

    def test_get_edge_by_id_existing(self, edge_controller_instance, sample_edge_response):
        """
        Test retrieving an existing edge by its ID.
        """
        # Mock the service to return the sample_edge_response
        edge_controller_instance.edge_service.get_edge_by_id.return_value = sample_edge_response

        # Invoke the controller's get_edge_by_id method
        result = edge_controller_instance.get_edge_by_id(sample_edge_response.edge_id)

        # Assertions
        assert isinstance(result, EdgeResponseSchema)
        assert result.edge_id == sample_edge_response.edge_id
        assert result.name == sample_edge_response.name

        # Ensure that audit_log was created
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()

    def test_get_edge_by_id_non_existing(self, edge_controller_instance):
        """
        Test retrieving a non-existing edge by its ID, expecting a 404 error.
        """
        non_existing_id = generate_uuid()

        # Mock the service to return None, indicating not found
        edge_controller_instance.edge_service.get_edge_by_id.return_value = None

        # Invoke the controller's get_edge_by_id method and expect an HTTPException
        with pytest.raises(HTTPException) as exc_info:
            edge_controller_instance.get_edge_by_id(non_existing_id)

        # Assertions
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Edge not found."

        # Ensure that audit_log was created with correct details
        edge_controller_instance.audit_service.create_audit_log.assert_called_once_with({
            "user_id": None,
            "action_type": "READ",
            "entity_type": "edge",
            "entity_id": str(non_existing_id),
            "details": "Edge not found."
        })

    # -------------------
    # Update Edge Tests
    # -------------------

    def test_update_edge_with_full_data(self, edge_controller_instance, sample_edge_update_full, sample_edge_response):
        """
        Test updating an edge with complete data.
        """
        # Mock the service to return the updated edge_response
        updated_response = EdgeResponseSchema(
            edge_id=sample_edge_response.edge_id,
            name=sample_edge_update_full.name,
            edge_type=sample_edge_update_full.edge_type,
            description=sample_edge_update_full.description,
            created_at=sample_edge_response.created_at,
            updated_at=datetime.utcnow(),
            created_by=sample_edge_response.created_by
        )
        edge_controller_instance.edge_service.update_edge.return_value = updated_response

        # Invoke the controller's update_edge method
        result = edge_controller_instance.update_edge(sample_edge_response.edge_id, sample_edge_update_full)

        # Assertions
        assert isinstance(result, EdgeResponseSchema)
        assert result.name == sample_edge_update_full.name
        assert result.edge_type == sample_edge_update_full.edge_type
        assert result.description == sample_edge_update_full.description

        # Ensure that audit_log was created
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()

    def test_update_edge_with_partial_data(self, edge_controller_instance, sample_edge_update_partial, sample_edge_response):
        """
        Test updating an edge with partial data.
        """
        # Mock the service to return the partially updated edge_response
        partially_updated_response = EdgeResponseSchema(
            edge_id=sample_edge_response.edge_id,
            name=sample_edge_response.name,  # Name remains unchanged
            edge_type=sample_edge_response.edge_type,  # Edge type remains unchanged
            description=sample_edge_update_partial.description,  # Description updated
            created_at=sample_edge_response.created_at,
            updated_at=datetime.utcnow(),
            created_by=sample_edge_response.created_by
        )
        edge_controller_instance.edge_service.update_edge.return_value = partially_updated_response

        # Invoke the controller's update_edge method
        result = edge_controller_instance.update_edge(sample_edge_response.edge_id, sample_edge_update_partial)

        # Assertions
        assert isinstance(result, EdgeResponseSchema)
        assert result.name == sample_edge_response.name
        assert result.edge_type == sample_edge_response.edge_type
        assert result.description == sample_edge_update_partial.description

        # Ensure that audit_log was created
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()

    def test_update_edge_with_invalid_edge_type(self, edge_controller_instance, sample_edge_update_full):
        """
        Test updating an edge with an invalid edge_type, expecting failure.
        """
        # Mock the service to return None, indicating failure
        edge_controller_instance.edge_service.update_edge.return_value = None

        # Invoke the controller's update_edge method and expect an HTTPException
        with pytest.raises(HTTPException) as exc_info:
            edge_controller_instance.update_edge(generate_uuid(), sample_edge_update_full)

        # Assertions
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "Edge update failed due to invalid data."

        # Ensure that audit_log was not created
        edge_controller_instance.audit_service.create_audit_log.assert_not_called()

    # -------------------
    # Delete Edge Tests
    # -------------------

    def test_delete_edge_existing(self, edge_controller_instance, sample_edge_response):
        """
        Test deleting an existing edge.
        """
        # Mock the service to return True, indicating successful deletion
        edge_controller_instance.edge_service.delete_edge.return_value = True

        # Invoke the controller's delete_edge method
        result = edge_controller_instance.delete_edge(sample_edge_response.edge_id)

        # Assertions
        assert result is True

        # Ensure that audit_log was created
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()

    def test_delete_edge_non_existing(self, edge_controller_instance):
        """
        Test deleting a non-existing edge, expecting failure.
        """
        non_existing_id = generate_uuid()

        # Mock the service to return False, indicating deletion failure
        edge_controller_instance.edge_service.delete_edge.return_value = False

        # Invoke the controller's delete_edge method and expect an HTTPException
        with pytest.raises(HTTPException) as exc_info:
            edge_controller_instance.delete_edge(non_existing_id)

        # Assertions
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "Edge deletion failed."

        # Ensure that audit_log was not created
        edge_controller_instance.audit_service.create_audit_log.assert_not_called()

    # -------------------
    # List Edges Tests
    # -------------------

    def test_list_edges_without_filters(self, edge_controller_instance, sample_edge_response):
        """
        Test listing edges without any filters.
        """
        # Mock the service to return a list of edges
        edge_controller_instance.edge_service.list_edges.return_value = [sample_edge_response]

        # Invoke the controller's list_edges method
        result = edge_controller_instance.list_edges()

        # Assertions
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].edge_id == sample_edge_response.edge_id

        # Ensure that audit_log was created
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()

    def test_list_edges_with_filters(self, edge_controller_instance, sample_edge_response):
        """
        Test listing edges with specific filters.
        """
        filters = {"edge_type": EdgeTypeEnum.primary.value}

        # Mock the service to return a filtered list of edges
        edge_controller_instance.edge_service.list_edges.return_value = [sample_edge_response]

        # Invoke the controller's list_edges method with filters
        result = edge_controller_instance.list_edges(filters=filters)

        # Assertions
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].edge_type == EdgeTypeEnum.primary

        # Ensure that audit_log was created
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()

    def test_list_edges_with_pagination(self, edge_controller_instance, sample_edge_response):
        """
        Test listing edges with pagination parameters.
        """
        limit = 10
        offset = 20

        # Mock the service to return a paginated list of edges
        edge_controller_instance.edge_service.list_edges.return_value = [sample_edge_response]

        # Invoke the controller's list_edges method with pagination
        result = edge_controller_instance.list_edges(limit=limit, offset=offset)

        # Assertions
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].edge_id == sample_edge_response.edge_id

        # Ensure that audit_log was created with correct parameters
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()

    # -------------------
    # Search Edges Tests
    # -------------------

    def test_search_edges_with_valid_parameters(self, edge_controller_instance, sample_edge_response):
        """
        Test searching edges with valid query parameters.
        """
        query_params = {"name": "FullEdge123"}  # Align with sample_edge_response.name

        # Mock the service to return a list of matching edges
        edge_controller_instance.edge_service.search_edges.return_value = [sample_edge_response]
        edge_controller_instance.edge_service.count_edges.return_value = 1

        # Invoke the controller's search_edges method
        result = edge_controller_instance.search_edges(query_params=query_params, limit=10, offset=0)

        # Assertions
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].name == "FullEdge123"  # Align with fixture

        # Ensure that audit_log was created
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()

    def test_search_edges_with_invalid_parameters(self, edge_controller_instance):
        """
        Test searching edges with invalid query parameters, expecting failure.
        """
        invalid_query_params = {"edge_type": "invalid_type"}

        # Mock the service to return an empty list and count as 0
        edge_controller_instance.edge_service.search_edges.return_value = []
        edge_controller_instance.edge_service.count_edges.return_value = 0

        # Invoke the controller's search_edges method
        result = edge_controller_instance.search_edges(query_params=invalid_query_params, limit=10, offset=0)

        # Assertions
        assert isinstance(result, list)
        assert len(result) == 0

        # Ensure that audit_log was created
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()

    # -------------------
    # Additional Edge Cases
    # -------------------

    def test_create_edge_with_duplicate_name(self, edge_controller_instance, sample_edge_create_full):
        """
        Test creating an edge with a duplicate name, expecting failure.
        """
        # Mock the service to return None, indicating failure due to duplicate
        edge_controller_instance.edge_service.create_edge.return_value = None

        # Invoke the controller's create_edge method and expect an HTTPException
        with pytest.raises(HTTPException) as exc_info:
            edge_controller_instance.create_edge(sample_edge_create_full)

        # Assertions
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "Edge creation failed due to invalid data."

        # Ensure that audit_log was not created
        edge_controller_instance.audit_service.create_audit_log.assert_not_called()

    def test_update_edge_with_no_data(self, edge_controller_instance, sample_edge_response):
        """
        Test updating an edge without providing any update data, expecting failure.
        """
        # Create an EdgeUpdateSchema with no data
        empty_update = EdgeUpdateSchema()

        # Mock the service to return None, indicating no update was performed
        edge_controller_instance.edge_service.update_edge.return_value = None

        # Invoke the controller's update_edge method and expect an HTTPException
        with pytest.raises(HTTPException) as exc_info:
            edge_controller_instance.update_edge(sample_edge_response.edge_id, empty_update)

        # Assertions
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "Edge update failed due to invalid data."

        # Ensure that audit_log was not created
        edge_controller_instance.audit_service.create_audit_log.assert_not_called()

    def test_delete_edge_twice(self, edge_controller_instance, sample_edge_response):
        """
        Test deleting an edge twice, expecting the second deletion to fail.
        """
        # First deletion succeeds
        edge_controller_instance.edge_service.delete_edge.return_value = True

        # Invoke the controller's delete_edge method
        result = edge_controller_instance.delete_edge(sample_edge_response.edge_id)
        assert result is True

        # Ensure that audit_log was created
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()

        # Second deletion fails
        edge_controller_instance.audit_service.create_audit_log.reset_mock()
        edge_controller_instance.edge_service.delete_edge.return_value = False

        # Invoke the controller's delete_edge method again and expect an HTTPException
        with pytest.raises(HTTPException) as exc_info:
            edge_controller_instance.delete_edge(sample_edge_response.edge_id)

        # Assertions
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "Edge deletion failed."

        # Ensure that audit_log was not created for the failed deletion
        edge_controller_instance.audit_service.create_audit_log.assert_not_called()

    def test_verify_edge_can_connect(self, edge_controller_instance):
        """
        Test verifying that an edge can connect two blocks.
        """
        # Arrange
        source_block_id = uuid4()
        target_block_id = uuid4()
        verification_request = EdgeVerificationRequestSchema(
            source_block_id=source_block_id,
            target_block_id=target_block_id
        )
        verification_response = EdgeVerificationResponseSchema(
            can_connect=True,
            reasons=[],
            existing_edges=[],
            verification_id=uuid4(),
            edge_version_id=uuid4(),
            verification_status="passed",
            verification_logs=None,
            verified_at=None,
            verified_by=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        edge_controller_instance.edge_service.can_connect_blocks.return_value = verification_response

        # Act
        result = edge_controller_instance.verify_edge(verification_request)

        # Assert
        assert isinstance(result, EdgeVerificationResponseSchema)
        assert result.can_connect is True
        assert len(result.reasons) == 0
        assert len(result.existing_edges) == 0
        assert result.verification_status == "passed"
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()
        edge_controller_instance.logger.log.assert_called()

    def test_verify_edge_cannot_connect_due_to_existing_edge(self, edge_controller_instance):
        """
        Test verifying that an edge cannot connect two blocks due to an existing edge.
        """
        source_block_id = uuid4()
        target_block_id = uuid4()
        verification_request = EdgeVerificationRequestSchema(
            source_block_id=source_block_id,
            target_block_id=target_block_id
        )
        existing_edge = EdgeResponseSchema(
            edge_id=uuid4(),
            name="ExistingEdge",
            edge_type=EdgeTypeEnum.primary,
            description="Existing edge between blocks",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=uuid4()
        )
        verification_response = EdgeVerificationResponseSchema(
            can_connect=False,
            reasons=["An edge already exists between these blocks."],
            existing_edges=[existing_edge],
            verification_id=uuid4(),
            edge_version_id=uuid4(),
            verification_status="failed",
            verification_logs=None,
            verified_at=None,
            verified_by=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        edge_controller_instance.edge_service.can_connect_blocks.return_value = verification_response

        # Act
        result = edge_controller_instance.verify_edge(verification_request)

        # Assert
        assert isinstance(result, EdgeVerificationResponseSchema)
        assert result.can_connect is False
        assert "An edge already exists between these blocks." in result.reasons
        assert len(result.existing_edges) == 1
        assert result.existing_edges[0].edge_id == existing_edge.edge_id
        assert result.verification_status == "failed"
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()
        edge_controller_instance.logger.log.assert_called()

    def test_verify_edge_can_connect_no_existing_edges(self, edge_controller_instance):
        """
        Test verifying that an edge can connect two blocks when there are no existing edges.
        """
        source_block_id = uuid4()
        target_block_id = uuid4()
        verification_request = EdgeVerificationRequestSchema(
            source_block_id=source_block_id,
            target_block_id=target_block_id
        )
        verification_response = EdgeVerificationResponseSchema(
            can_connect=True,
            reasons=[],
            existing_edges=[],
            verification_id=uuid4(),
            edge_version_id=uuid4(),
            verification_status="passed",
            verification_logs=None,
            verified_at=None,
            verified_by=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        edge_controller_instance.edge_service.can_connect_blocks.return_value = verification_response

        # Act
        result = edge_controller_instance.verify_edge(verification_request)

        # Assert
        assert isinstance(result, EdgeVerificationResponseSchema)
        assert result.can_connect is True
        assert len(result.reasons) == 0
        assert len(result.existing_edges) == 0
        assert result.verification_status == "passed"
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()
        edge_controller_instance.logger.log.assert_called()

    def test_verify_edge_cannot_connect_due_to_incompatible_block_types(self, edge_controller_instance):
        """
        Test verifying that an edge cannot connect two blocks due to incompatible block types.
        """
        source_block_id = uuid4()
        target_block_id = uuid4()
        verification_request = EdgeVerificationRequestSchema(
            source_block_id=source_block_id,
            target_block_id=target_block_id
        )
        verification_response = EdgeVerificationResponseSchema(
            can_connect=False,
            reasons=["Incompatible block types: Cannot connect a 'data' block to a 'visualization' block."],
            existing_edges=[],
            verification_id=uuid4(),
            edge_version_id=uuid4(),
            verification_status="failed",
            verification_logs=None,
            verified_at=None,
            verified_by=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        edge_controller_instance.edge_service.can_connect_blocks.return_value = verification_response

        # Act
        result = edge_controller_instance.verify_edge(verification_request)

        # Assert
        assert isinstance(result, EdgeVerificationResponseSchema)
        assert result.can_connect is False
        assert "Incompatible block types" in result.reasons[0]
        assert len(result.existing_edges) == 0
        assert result.verification_status == "failed"
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()
        edge_controller_instance.logger.log.assert_called()

    def test_verify_edge_cannot_connect_due_to_cycle_creation(self, edge_controller_instance):
        """
        Test verifying that an edge cannot connect two blocks because it would create a cycle in the pipeline.
        """
        source_block_id = uuid4()
        target_block_id = uuid4()
        verification_request = EdgeVerificationRequestSchema(
            source_block_id=source_block_id,
            target_block_id=target_block_id
        )
        verification_response = EdgeVerificationResponseSchema(
            can_connect=False,
            reasons=["Connecting these blocks would create a cycle in the pipeline."],
            existing_edges=[],
            verification_id=uuid4(),
            edge_version_id=uuid4(),
            verification_status="failed",
            verification_logs=None,
            verified_at=None,
            verified_by=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        edge_controller_instance.edge_service.can_connect_blocks.return_value = verification_response

        # Act
        result = edge_controller_instance.verify_edge(verification_request)

        # Assert
        assert isinstance(result, EdgeVerificationResponseSchema)
        assert result.can_connect is False
        assert "create a cycle" in result.reasons[0]
        assert len(result.existing_edges) == 0
        assert result.verification_status == "failed"
        edge_controller_instance.audit_service.create_audit_log.assert_called_once()
        edge_controller_instance.logger.log.assert_called()