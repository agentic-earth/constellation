# test_edge_controller.py

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID
from backend.app.features.core.controllers.edge_controller import EdgeController

# Fixture to provide a consistent user_id for all tests
@pytest.fixture
def user_id():
    return UUID('123e4567-e89b-12d3-a456-426614174000')

# Test for the create_edge method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.edge_controller.Prisma')
async def test_create_edge(prisma_mock, user_id):
    """
    Test the create_edge method of EdgeController.
    This test checks if an edge can be successfully created and returned.
    """

    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the EdgeController with the mocked Prisma client
    controller = EdgeController(prisma_mock.return_value)

    # Mock the EdgeService's create_edge method
    mock_edge = MagicMock()
    mock_edge.edge_id = '123e4567-e89b-12d3-a456-426614174001'
    mock_edge.source_block_id = '123e4567-e89b-12d3-a456-426614174002'
    mock_edge.target_block_id = '123e4567-e89b-12d3-a456-426614174003'
    mock_edge.dict.return_value = {
        'edge_id': mock_edge.edge_id,
        'source_block_id': mock_edge.source_block_id,
        'target_block_id': mock_edge.target_block_id
    }

    # Replace the EdgeService in the controller with a mock
    edge_service_mock = AsyncMock()
    edge_service_mock.create_edge.return_value = mock_edge
    controller.edge_service = edge_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Define the edge data to be used in the test
    edge_data = {
        'source_block_id': '123e4567-e89b-12d3-a456-426614174002',
        'target_block_id': '123e4567-e89b-12d3-a456-426614174003'
    }

    # Call the create_edge method of the controller
    result = await controller.create_edge(edge_data, user_id)

    # Assertions to verify the result
    assert result is not None
    assert result['edge_id'] == '123e4567-e89b-12d3-a456-426614174001'
    assert result['source_block_id'] == '123e4567-e89b-12d3-a456-426614174002'
    assert result['target_block_id'] == '123e4567-e89b-12d3-a456-426614174003'

# Test for the get_edge method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.edge_controller.Prisma')
async def test_get_edge(prisma_mock, user_id):
    """
    Test the get_edge method of EdgeController.
    This test checks if an edge can be successfully retrieved by its ID.
    """

    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the EdgeController with the mocked Prisma client
    controller = EdgeController(prisma_mock.return_value)

    # Mock the EdgeService's get_edge_by_id method
    mock_edge = MagicMock()
    mock_edge.edge_id = '123e4567-e89b-12d3-a456-426614174001'
    mock_edge.source_block_id = '123e4567-e89b-12d3-a456-426614174002'
    mock_edge.target_block_id = '123e4567-e89b-12d3-a456-426614174003'
    mock_edge.dict.return_value = {
        'edge_id': mock_edge.edge_id,
        'source_block_id': mock_edge.source_block_id,
        'target_block_id': mock_edge.target_block_id
    }

    # Replace the EdgeService in the controller with a mock
    edge_service_mock = AsyncMock()
    edge_service_mock.get_edge_by_id.return_value = mock_edge
    controller.edge_service = edge_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Call the get_edge method of the controller with a specific edge_id
    result = await controller.get_edge(UUID('123e4567-e89b-12d3-a456-426614174001'), user_id)

    # Assertions to verify the result
    assert result is not None
    assert result['edge_id'] == '123e4567-e89b-12d3-a456-426614174001'
    assert result['source_block_id'] == '123e4567-e89b-12d3-a456-426614174002'
    assert result['target_block_id'] == '123e4567-e89b-12d3-a456-426614174003'

# Test for the update_edge method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.edge_controller.Prisma')
async def test_update_edge(prisma_mock, user_id):
    """
    Test the update_edge method of EdgeController.
    This test checks if an edge can be successfully updated.
    """

    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the EdgeController with the mocked Prisma client
    controller = EdgeController(prisma_mock.return_value)

    # Mock the EdgeService's update_edge method
    mock_edge = MagicMock()
    mock_edge.edge_id = '123e4567-e89b-12d3-a456-426614174001'
    mock_edge.source_block_id = '123e4567-e89b-12d3-a456-426614174004'  # Updated source_block_id
    mock_edge.target_block_id = '123e4567-e89b-12d3-a456-426614174005'  # Updated target_block_id
    mock_edge.dict.return_value = {
        'edge_id': mock_edge.edge_id,
        'source_block_id': mock_edge.source_block_id,
        'target_block_id': mock_edge.target_block_id
    }

    # Replace the EdgeService in the controller with a mock
    edge_service_mock = AsyncMock()
    edge_service_mock.update_edge.return_value = mock_edge
    controller.edge_service = edge_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Define the update data for the edge
    update_data = {
        'source_block_id': '123e4567-e89b-12d3-a456-426614174004',
        'target_block_id': '123e4567-e89b-12d3-a456-426614174005'
    }

    # Call the update_edge method of the controller
    result = await controller.update_edge(UUID('123e4567-e89b-12d3-a456-426614174001'), update_data, user_id)

    # Assertions to verify the result
    assert result is not None
    assert result['edge_id'] == '123e4567-e89b-12d3-a456-426614174001'
    assert result['source_block_id'] == '123e4567-e89b-12d3-a456-426614174004'
    assert result['target_block_id'] == '123e4567-e89b-12d3-a456-426614174005'

# Test for the delete_edge method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.edge_controller.Prisma')
async def test_delete_edge(prisma_mock, user_id):
    """
    Test the delete_edge method of EdgeController.
    This test checks if an edge can be successfully deleted.
    """

    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the EdgeController with the mocked Prisma client
    controller = EdgeController(prisma_mock.return_value)

    # Mock the EdgeService's delete_edge method to return True (success)
    edge_service_mock = AsyncMock()
    edge_service_mock.delete_edge.return_value = True
    controller.edge_service = edge_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Call the delete_edge method of the controller
    result = await controller.delete_edge(UUID('123e4567-e89b-12d3-a456-426614174001'), user_id)

    # Assertion to verify that the edge was deleted successfully
    assert result is True

# Test for the list_edges method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.edge_controller.Prisma')
async def test_list_edges(prisma_mock, user_id):
    """
    Test the list_edges method of EdgeController.
    This test checks if edges can be successfully listed.
    """

    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the EdgeController with the mocked Prisma client
    controller = EdgeController(prisma_mock.return_value)

    # Mock two edge objects to be returned by the list_edges method
    mock_edge1 = MagicMock()
    mock_edge1.edge_id = '123e4567-e89b-12d3-a456-426614174001'
    mock_edge1.source_block_id = '123e4567-e89b-12d3-a456-426614174002'
    mock_edge1.target_block_id = '123e4567-e89b-12d3-a456-426614174003'
    mock_edge1.dict.return_value = {
        'edge_id': mock_edge1.edge_id,
        'source_block_id': mock_edge1.source_block_id,
        'target_block_id': mock_edge1.target_block_id
    }

    mock_edge2 = MagicMock()
    mock_edge2.edge_id = '123e4567-e89b-12d3-a456-426614174004'
    mock_edge2.source_block_id = '123e4567-e89b-12d3-a456-426614174005'
    mock_edge2.target_block_id = '123e4567-e89b-12d3-a456-426614174006'
    mock_edge2.dict.return_value = {
        'edge_id': mock_edge2.edge_id,
        'source_block_id': mock_edge2.source_block_id,
        'target_block_id': mock_edge2.target_block_id
    }

    # Replace the EdgeService in the controller with a mock
    edge_service_mock = AsyncMock()
    edge_service_mock.list_edges.return_value = [mock_edge1, mock_edge2]
    controller.edge_service = edge_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Define filters for listing edges (empty in this case)
    filters = {}

    # Call the list_edges method of the controller
    result = await controller.list_edges(user_id, filters)

    # Assertions to verify the result
    assert result is not None
    assert len(result) == 2
    assert result[0]['edge_id'] == '123e4567-e89b-12d3-a456-426614174001'
    assert result[1]['edge_id'] == '123e4567-e89b-12d3-a456-426614174004'

