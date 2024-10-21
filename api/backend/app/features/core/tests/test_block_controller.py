import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID
from backend.app.features.core.controllers.block_controller import BlockController



@pytest.fixture
def user_id():
    return UUID('123e4567-e89b-12d3-a456-426614174000')

@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.block_controller.Prisma')
async def test_create_block(prisma_mock, user_id):
    # Create a mock transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the controller with the mocked Prisma client
    controller = BlockController(prisma_mock.return_value)

    # Mock BlockService response
    mock_block = MagicMock()
    mock_block.block_id = '123e4567-e89b-12d3-a456-426614174001'  # Use string instead of UUID

    # Mock the dict() method to return block_id as a string
    mock_block.dict.return_value = {
    "block_id": mock_block.block_id  # It's already a string
    }
    
    block_service_mock = AsyncMock()
    block_service_mock.create_block.return_value = mock_block
    controller.block_service = block_service_mock

    # Mock TaxonomyService response
    taxonomy_service_mock = AsyncMock()
    taxonomy_service_mock.create_taxonomy_for_block.return_value = True
    controller.taxonomy_service = taxonomy_service_mock

    # Mock AuditService response
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Define the block data
    create_schema = {
        "name": "TestBlock",
        "block_type": "model",
        "description": "A test block.",
        "taxonomy": {
            "general": {
                "categories": [{"name": "Category1"}]
            }
        }
    }

    print("Calling create_block...")
    result = await controller.create_block(create_schema, user_id)
    print(f"Result from create_block: {result}")
    
    # Assert that the result is not None and contains the correct block_id as a string
    assert result is not None
    assert result['block_id'] == '123e4567-e89b-12d3-a456-426614174001'


@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.block_controller.Prisma')
async def test_get_block_by_id(prisma_mock, user_id):
    # Create a mock transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the controller with the mocked Prisma client
    controller = BlockController(prisma_mock.return_value)

    # Mock the get_block_by_id service
    block_service_mock = AsyncMock()
    block_service_mock.get_block_by_id.return_value = MagicMock(
        block_id=UUID('123e4567-e89b-12d3-a456-426614174001'), 
        dict=lambda: {"block_id": "123e4567-e89b-12d3-a456-426614174001"}
    )
    controller.block_service = block_service_mock

    # Test retrieving block by ID
    result = await controller.get_block_by_id(UUID('123e4567-e89b-12d3-a456-426614174001'), user_id)
    assert result is not None
    assert result['block_id'] == '123e4567-e89b-12d3-a456-426614174001'

@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.block_controller.Prisma')
async def test_update_block(prisma_mock, user_id):
    # Create a mock transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the controller with the mocked Prisma client
    controller = BlockController(prisma_mock.return_value)

    # Mock the update_block service
    block_service_mock = AsyncMock()
    block_service_mock.update_block.return_value = MagicMock(
        block_id=UUID('123e4567-e89b-12d3-a456-426614174001'), 
        dict=lambda: {"block_id": "123e4567-e89b-12d3-a456-426614174001"}
    )
    controller.block_service = block_service_mock

    # Mock the taxonomy service for the update
    taxonomy_service_mock = AsyncMock()
    taxonomy_service_mock.create_taxonomy_for_block.return_value = True
    controller.taxonomy_service = taxonomy_service_mock

    # Test block update
    update_schema = {"name": "UpdatedBlock"}
    result = await controller.update_block(UUID('123e4567-e89b-12d3-a456-426614174001'), update_schema, user_id)
    assert result is not None
    assert result['block_id'] == '123e4567-e89b-12d3-a456-426614174001'

@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.block_controller.Prisma')
async def test_delete_block(prisma_mock, user_id):
    # Create a mock transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the controller with the mocked Prisma client
    controller = BlockController(prisma_mock.return_value)

    # Mock the delete_block service
    block_service_mock = AsyncMock()
    block_service_mock.delete_block.return_value = True
    controller.block_service = block_service_mock

    # Mock audit logging for deletion
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Test block deletion
    result = await controller.delete_block(UUID('123e4567-e89b-12d3-a456-426614174001'), user_id)
    assert result is True

@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.block_controller.Prisma')
async def test_search_blocks(prisma_mock, user_id):
    # Create a mock transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the controller with the mocked Prisma client
    controller = BlockController(prisma_mock.return_value)

    # Mock the taxonomy service search
    taxonomy_service_mock = AsyncMock()
    taxonomy_service_mock.search_blocks.return_value = [
        MagicMock(block_id=UUID('123e4567-e89b-12d3-a456-426614174001'), dict=lambda: {"block_id": "123e4567-e89b-12d3-a456-426614174001"})
    ]
    controller.taxonomy_service = taxonomy_service_mock

    # Test block search
    search_filters = {"category_names": ["Climate Data"], "block_types": ["model"]}
    result = await controller.search_blocks(search_filters, user_id)
    assert result is not None
    assert len(result) == 1
    assert result[0]['block_id'] == '123e4567-e89b-12d3-a456-426614174001'

