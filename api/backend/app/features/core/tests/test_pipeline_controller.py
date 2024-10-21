# test_pipeline_controller.py

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID
from backend.app.features.core.controllers.pipeline_controller import PipelineController
from collections import UserDict

# Custom AttrDict class to allow attribute access to dictionary items
class AttrDict(UserDict):
    """A dictionary that supports attribute access."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
        
@pytest.fixture
def pipeline_id():
    return UUID('223e4567-e89b-12d3-a456-426614174001')

# Fixture to provide a consistent user_id for all tests
@pytest.fixture
def user_id():
    return UUID('123e4567-e89b-12d3-a456-426614174000')

# Test for the create_pipeline method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.pipeline_controller.Prisma')
async def test_create_pipeline(prisma_mock, user_id):
    """
    Test the create_pipeline method of PipelineController.
    This test checks if a pipeline can be successfully created and returned.
    """

    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the PipelineController with the mocked Prisma client
    controller = PipelineController(prisma_mock.return_value)

    # Mock the PipelineService's create_pipeline method
    mock_pipeline = MagicMock()
    mock_pipeline.pipeline_id = '123e4567-e89b-12d3-a456-426614174001'
    mock_pipeline.name = 'Test Pipeline'
    mock_pipeline.description = 'This is a test pipeline.'
    mock_pipeline.dict.return_value = {
        'pipeline_id': mock_pipeline.pipeline_id,
        'name': mock_pipeline.name,
        'description': mock_pipeline.description
    }

    # Replace the PipelineService in the controller with a mock
    pipeline_service_mock = AsyncMock()

    # Mock the create_pipeline method to accept tx and pipeline_data and return mock_pipeline
    async def mock_create_pipeline(tx, pipeline_data):
        return mock_pipeline  # Return the mock_pipeline regardless of input

    pipeline_service_mock.create_pipeline = AsyncMock(side_effect=mock_create_pipeline)
    controller.pipeline_service = pipeline_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()

    # Mock the create_audit_log method to accept tx and audit_log and return True
    async def mock_create_audit_log(tx, audit_log):
        return True

    audit_service_mock.create_audit_log = AsyncMock(side_effect=mock_create_audit_log)
    controller.audit_service = audit_service_mock

    # Define the pipeline data to be used in the test, using AttrDict
    pipeline_data = AttrDict({
        'name': 'Test Pipeline',
        'description': 'This is a test pipeline.',
        'created_by': str(user_id)
    })

    # Call the create_pipeline method of the controller
    result = await controller.create_pipeline(pipeline_data, user_id)

    # Assertions to verify the result
    assert result is not None
    assert result['pipeline_id'] == '123e4567-e89b-12d3-a456-426614174001'
    assert result['name'] == 'Test Pipeline'
    assert result['description'] == 'This is a test pipeline.'

# Test for the get_pipeline_by_id method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.pipeline_controller.Prisma')
async def test_get_pipeline_by_id(prisma_mock, user_id):
    """
    Test the get_pipeline_by_id method of PipelineController.
    This test checks if a pipeline can be successfully retrieved by its ID.
    """

    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the PipelineController with the mocked Prisma client
    controller = PipelineController(prisma_mock.return_value)

    # Mock the PipelineService's get_pipeline_by_id method
    mock_pipeline = MagicMock()
    mock_pipeline.pipeline_id = '123e4567-e89b-12d3-a456-426614174001'
    mock_pipeline.name = 'Test Pipeline'
    mock_pipeline.description = 'This is a test pipeline.'
    mock_pipeline.dict.return_value = {
        'pipeline_id': mock_pipeline.pipeline_id,
        'name': mock_pipeline.name,
        'description': mock_pipeline.description
    }

    # Replace the PipelineService in the controller with a mock
    pipeline_service_mock = AsyncMock()
    pipeline_service_mock.get_pipeline_by_id.return_value = mock_pipeline
    controller.pipeline_service = pipeline_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Call the get_pipeline_by_id method of the controller with a specific pipeline_id
    result = await controller.get_pipeline_by_id(UUID('123e4567-e89b-12d3-a456-426614174001'), user_id)

    # Assertions to verify the result
    assert result is not None
    assert result['pipeline_id'] == '123e4567-e89b-12d3-a456-426614174001'
    assert result['name'] == 'Test Pipeline'
    assert result['description'] == 'This is a test pipeline.'

# Test for the update_pipeline method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.pipeline_controller.Prisma')
async def test_update_pipeline(prisma_mock, user_id):
    """
    Test the update_pipeline method of PipelineController.
    This test checks if a pipeline can be successfully updated.
    """

    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the PipelineController with the mocked Prisma client
    controller = PipelineController(prisma_mock.return_value)

    # Mock the PipelineService's update_pipeline method
    mock_pipeline = MagicMock()
    mock_pipeline.pipeline_id = '123e4567-e89b-12d3-a456-426614174001'
    mock_pipeline.name = 'Updated Test Pipeline'
    mock_pipeline.description = 'This is an updated test pipeline.'
    mock_pipeline.dict.return_value = {
        'pipeline_id': mock_pipeline.pipeline_id,
        'name': mock_pipeline.name,
        'description': mock_pipeline.description
    }

    # Replace the PipelineService in the controller with a mock
    pipeline_service_mock = AsyncMock()
    pipeline_service_mock.update_pipeline.return_value = mock_pipeline
    controller.pipeline_service = pipeline_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Define the update data for the pipeline
    update_data = {
        'name': 'Updated Test Pipeline',
        'description': 'This is an updated test pipeline.'
    }

    # Call the update_pipeline method of the controller
    result = await controller.update_pipeline(UUID('123e4567-e89b-12d3-a456-426614174001'), update_data, user_id)

    # Assertions to verify the result
    assert result is not None
    assert result['pipeline_id'] == '123e4567-e89b-12d3-a456-426614174001'
    assert result['name'] == 'Updated Test Pipeline'
    assert result['description'] == 'This is an updated test pipeline.'

# test_pipeline_controller.py

@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.pipeline_controller.Prisma')
async def test_delete_pipeline(prisma_mock, pipeline_id, user_id):
    # Mock transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the controller with the mocked Prisma client
    controller = PipelineController(prisma_mock.return_value)

    # Mock PipelineService
    pipeline_service_mock = AsyncMock()
    pipeline_service_mock.delete_pipeline.return_value = True  # Simulate successful deletion
    controller.pipeline_service = pipeline_service_mock

    # Mock AuditService
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Call delete_pipeline and verify the result
    result = await controller.delete_pipeline(pipeline_id, user_id)

    # Assert that deletion was successful
    assert result is True, "Pipeline deletion failed even though the mock should return True."

    # Ensure delete_pipeline was called with the transaction
    pipeline_service_mock.delete_pipeline.assert_called_once_with(tx_mock, pipeline_id)

    # Ensure audit log creation was called with the transaction
    audit_service_mock.create_audit_log.assert_called_once_with(tx_mock, {
        'user_id': str(user_id),
        'action_type': 'DELETE',
        'entity_type': 'pipeline',
        'entity_id': str(pipeline_id),
        'details': {
            'pipeline_id': str(pipeline_id),
        },
    })

    # Assert that the Prisma transaction was used
    assert prisma_mock.return_value.tx.called is True, "Prisma transaction mock was not called."





@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.pipeline_controller.Prisma')
async def test_list_pipelines(prisma_mock, user_id):
    # Mock transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the controller with the mocked Prisma client
    controller = PipelineController(prisma_mock.return_value)

    # Mock PipelineService to return a non-empty list of pipelines
    pipeline_service_mock = AsyncMock()
    mock_pipeline = MagicMock(pipeline_id=UUID('323e4567-e89b-12d3-a456-426614174002'))
    mock_pipeline.dict.return_value = {"pipeline_id": str(mock_pipeline.pipeline_id)}
    pipeline_service_mock.list_pipelines.return_value = [mock_pipeline]
    controller.pipeline_service = pipeline_service_mock

    # Mock AuditService
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Debug: Print whether the Prisma transaction was called
    print(f"Prisma transaction mock called: {prisma_mock.return_value.tx.called}")
    
    # Call list_pipelines and verify the result
    filters = {"name": "Test Pipeline"}
    
    print("Calling controller.list_pipelines()...")
    result = await controller.list_pipelines(user_id, filters=filters)
    
    # Debug: Print result and ensure list_pipelines was called
    print(f"Result from list_pipelines: {result}")
    print(f"Was list_pipelines called on mock?: {pipeline_service_mock.list_pipelines.called}")
    print(f"Parameters passed to list_pipelines: {pipeline_service_mock.list_pipelines.call_args}")

    # Ensure list_pipelines is called
    assert pipeline_service_mock.list_pipelines.called, "list_pipelines was not called."
    assert pipeline_service_mock.list_pipelines.call_count == 1, "list_pipelines was not called exactly once."

    # Check the parameters passed to list_pipelines
    pipeline_service_mock.list_pipelines.assert_called_once_with(tx_mock, filters, None, None)

    # Assert that the result contains exactly one pipeline
    assert len(result) == 1, f"Expected 1 pipeline but got {len(result)}" 
    assert result[0]["pipeline_id"] == "323e4567-e89b-12d3-a456-426614174002", "Unexpected pipeline_id"
    print(result)







# Test for the create_pipeline_with_dependencies method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.pipeline_controller.Prisma')
async def test_create_pipeline_with_dependencies(prisma_mock, user_id):
    """
    Test the create_pipeline_with_dependencies method of PipelineController.
    This test checks if a pipeline along with its blocks and edges can be successfully created.
    """

    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the PipelineController with the mocked Prisma client
    controller = PipelineController(prisma_mock.return_value)

    # Mock the PipelineService's create_pipeline method
    mock_pipeline = MagicMock()
    mock_pipeline.pipeline_id = '123e4567-e89b-12d3-a456-426614174001'
    mock_pipeline.name = 'Test Pipeline'
    mock_pipeline.description = 'This is a test pipeline.'
    mock_pipeline.dict.return_value = {
        'pipeline_id': mock_pipeline.pipeline_id,
        'name': mock_pipeline.name,
        'description': mock_pipeline.description
    }
    pipeline_service_mock = AsyncMock()
    pipeline_service_mock.create_pipeline.return_value = mock_pipeline
    controller.pipeline_service = pipeline_service_mock

    # Mock the BlockService's get_block_by_name and create_block methods
    mock_block = MagicMock()
    mock_block.block_id = '123e4567-e89b-12d3-a456-426614174002'
    mock_block.name = 'Test Block'
    mock_block.dict.return_value = {
        'block_id': mock_block.block_id,
        'name': mock_block.name
    }
    block_service_mock = AsyncMock()
    block_service_mock.get_block_by_name.return_value = None
    block_service_mock.create_block.return_value = mock_block
    controller.block_service = block_service_mock
    print("a")

    # Mock the PipelineService's assign_block_to_pipeline method
    pipeline_service_mock.assign_block_to_pipeline.return_value = True

    # Mock the EdgeService's create_edge method
    mock_edge = MagicMock()
    mock_edge.edge_id = '123e4567-e89b-12d3-a456-426614174003'
    mock_edge.dict.return_value = {
        'edge_id': mock_edge.edge_id
    }
    edge_service_mock = AsyncMock()
    edge_service_mock.create_edge.return_value = mock_edge
    controller.edge_service = edge_service_mock

    # Mock the PipelineService's assign_edge_to_pipeline method
    pipeline_service_mock.assign_edge_to_pipeline.return_value = True

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Define the pipeline data, blocks, and edges
    pipeline_data = {
        'name': 'Test Pipeline',
        'description': 'This is a test pipeline.',
        'created_by': str(user_id)
    }
    blocks = [
        {'name': 'Test Block', 'block_type': 'dataset', 'description': 'A test block.'}
    ]
    edges = [
        {'source_block_id': '123e4567-e89b-12d3-a456-426614174002', 'target_block_id': '123e4567-e89b-12d3-a456-426614174002'}
    ]

    # Call the create_pipeline_with_dependencies method
    result = await controller.create_pipeline_with_dependencies(pipeline_data, blocks, edges, user_id)

    # Assertions to verify the result
    assert result is not None
    assert result['pipeline_id'] == '123e4567-e89b-12d3-a456-426614174001'
    assert result['name'] == 'Test Pipeline'
    assert result['description'] == 'This is a test pipeline.'

# Test for the delete_pipeline_with_dependencies method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.pipeline_controller.Prisma')
async def test_delete_pipeline_with_dependencies(prisma_mock, user_id):
    """
    Test the delete_pipeline_with_dependencies method of PipelineController.
    This test checks if a pipeline along with its blocks and edges can be successfully deleted.
    """

    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the PipelineController with the mocked Prisma client
    controller = PipelineController(prisma_mock.return_value)

    # Mock the PipelineService's methods
    pipeline_service_mock = AsyncMock()
    # Mock get_pipeline_blocks and get_pipeline_edges
    pipeline_service_mock.get_pipeline_blocks.return_value = []
    pipeline_service_mock.get_pipeline_edges.return_value = []
    # Mock delete_pipeline
    pipeline_service_mock.delete_pipeline.return_value = True
    controller.pipeline_service = pipeline_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Call the delete_pipeline_with_dependencies method
    result = await controller.delete_pipeline_with_dependencies(UUID('123e4567-e89b-12d3-a456-426614174001'), user_id)

    # Assertion to verify that the pipeline and its dependencies were deleted successfully
    assert result is True

# Test for the verify_pipeline method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.pipeline_controller.Prisma')
async def test_verify_pipeline(prisma_mock, user_id):
    """
    Test the verify_pipeline method of PipelineController.
    This test checks if a pipeline can be successfully verified.
    """

    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the PipelineController with the mocked Prisma client
    controller = PipelineController(prisma_mock.return_value)

    # Mock the PipelineService's get_pipeline_edges method
    mock_pipeline_edge = MagicMock()
    mock_pipeline_edge.edge_id = '123e4567-e89b-12d3-a456-426614174003'
    pipeline_service_mock = AsyncMock()
    pipeline_service_mock.get_pipeline_edges.return_value = [mock_pipeline_edge]
    controller.pipeline_service = pipeline_service_mock

    # Mock the EdgeService's verify_edges and get_edge_by_id methods
    edge_service_mock = AsyncMock()
    edge_service_mock.verify_edges.return_value = True

    mock_edge = MagicMock()
    mock_edge.source_block_id = '123e4567-e89b-12d3-a456-426614174002'
    mock_edge.target_block_id = '123e4567-e89b-12d3-a456-426614174004'
    edge_service_mock.get_edge_by_id.return_value = mock_edge
    controller.edge_service = edge_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Call the verify_pipeline method
    result = await controller.verify_pipeline(UUID('123e4567-e89b-12d3-a456-426614174001'), user_id)

    # Assertion to verify that the pipeline is valid
    assert result is True
