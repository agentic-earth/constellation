# test_user_controller.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID
from backend.app.features.core.controllers.user_controller import UserController
from prisma import Prisma
from supabase import Client as SupabaseClient
from backend.app.logger import ConstellationLogger
from datetime import datetime, timedelta

# Fixture to provide a consistent user_id for all tests
@pytest.fixture
def user_id():
    return UUID('123e4567-e89b-12d3-a456-426614174000')

# Fixture to provide a mocked ConstellationLogger
@pytest.fixture
def logger():
    return ConstellationLogger()

# Test for the register_user method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.user_controller.Prisma')
@patch('backend.app.features.core.controllers.user_controller.Client')
async def test_register_user(supabase_client_mock, prisma_mock, user_id, logger):
    """
    Test the register_user method of UserController.
    This test checks if a user can be successfully registered.
    """
    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the UserController with the mocked Prisma and Supabase clients
    controller = UserController(
        prisma=prisma_mock.return_value,
        supabase=supabase_client_mock.return_value,
        supabase_admin=supabase_client_mock.return_value,
        logger=logger
    )

    # Mock the UserService's register_user_email_password method
    mock_profile = MagicMock()
    mock_profile.auth_uid = str(user_id)
    mock_profile.username = 'test_user'
    mock_profile.email = 'test_user@example.com'
    mock_profile.dict.return_value = {
        'auth_uid': mock_profile.auth_uid,
        'username': mock_profile.username,
        'email': mock_profile.email
    }

    registration_result = {
        'success': True,
        'profile': mock_profile,
        'message': 'User registered successfully.'
    }

    user_service_mock = AsyncMock()
    user_service_mock.register_user_email_password.return_value = registration_result
    controller.user_service = user_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Call the register_user method
    email = 'test_user@example.com'
    password = 'securePassword123!'
    username = 'test_user'
    result = await controller.register_user(email, password, username)

    # Assertions to verify the result
    assert result['success'] is True
    assert result['profile']['auth_uid'] == str(user_id)
    assert result['profile']['username'] == 'test_user'
    assert result['profile']['email'] == 'test_user@example.com'
    assert result['message'] == 'User registered successfully.'

# Test for the sign_in_user method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.user_controller.Prisma')
@patch('backend.app.features.core.controllers.user_controller.Client')
async def test_sign_in_user(supabase_client_mock, prisma_mock, user_id, logger):
    """
    Test the sign_in_user method of UserController.
    This test checks if a user can sign in successfully.
    """
    # Instantiate the UserController with the mocked Prisma and Supabase clients
    controller = UserController(
        prisma=prisma_mock.return_value,
        supabase=supabase_client_mock.return_value,
        supabase_admin=supabase_client_mock.return_value,
        logger=logger
    )

    # Mock the UserService's sign_in_user_email_password method
    sign_in_result = {
        'success': True,
        'user': {
            'id': str(user_id),
            'email': 'test_user@example.com'
        },
        'message': 'User signed in successfully.'
    }

    user_service_mock = AsyncMock()
    user_service_mock.sign_in_user_email_password.return_value = sign_in_result
    controller.user_service = user_service_mock

    # Call the sign_in_user method
    email = 'test_user@example.com'
    password = 'securePassword123!'
    result = await controller.sign_in_user(email, password)

    # Assertions to verify the result
    assert result['success'] is True
    assert result['user']['id'] == str(user_id)
    assert result['user']['email'] == 'test_user@example.com'
    assert result['message'] == 'User signed in successfully.'

# Test for the update_user_profile method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.user_controller.Prisma')
async def test_update_user_profile(prisma_mock, user_id, logger):
    """
    Test the update_user_profile method of UserController.
    This test checks if a user's profile can be updated successfully.
    """
    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the UserController with the mocked Prisma client
    controller = UserController(
        prisma=prisma_mock.return_value,
        supabase=None,
        supabase_admin=None,
        logger=logger
    )

    # Mock the UserService's update_profile method
    mock_profile = MagicMock()
    mock_profile.auth_uid = str(user_id)
    mock_profile.username = 'updated_user'
    mock_profile.dict.return_value = {
        'auth_uid': mock_profile.auth_uid,
        'username': mock_profile.username
    }

    user_service_mock = AsyncMock()
    user_service_mock.update_profile.return_value = mock_profile
    controller.user_service = user_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Call the update_user_profile method
    update_data = {'username': 'updated_user'}
    result = await controller.update_user_profile(user_id, update_data)

    # Assertions to verify the result
    assert result['success'] is True
    assert result['profile']['auth_uid'] == str(user_id)
    assert result['profile']['username'] == 'updated_user'
    assert result['message'] == 'User profile updated successfully.'

# Test for the delete_user method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.user_controller.Prisma')
@patch('backend.app.features.core.controllers.user_controller.Client')
async def test_delete_user(supabase_client_mock, prisma_mock, user_id, logger):
    """
    Test the delete_user method of UserController.
    This test checks if a user can be deleted successfully.
    """
    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the UserController with the mocked Prisma and Supabase clients
    controller = UserController(
        prisma=prisma_mock.return_value,
        supabase=supabase_client_mock.return_value,
        supabase_admin=supabase_client_mock.return_value,
        logger=logger
    )

    # Mock the ApiKeyService's get_api_keys_by_user and revoke_api_key methods
    api_key_service_mock = AsyncMock()
    api_key_mock = MagicMock()
    api_key_mock.api_key_id = '123e4567-e89b-12d3-a456-426614174001'
    api_key_service_mock.get_api_keys_by_user.return_value = [api_key_mock]
    api_key_service_mock.revoke_api_key.return_value = True
    controller.api_key_service = api_key_service_mock

    # Mock the UserService's delete_user method
    user_service_mock = AsyncMock()
    user_service_mock.delete_user.return_value = True
    controller.user_service = user_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Call the delete_user method
    result = await controller.delete_user(user_id)

    # Assertions to verify the result
    assert result['success'] is True
    assert result['message'] == 'User deleted successfully'

# Test for the list_api_keys_for_user method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.user_controller.Prisma')
async def test_list_api_keys_for_user(prisma_mock, user_id, logger):
    """
    Test the list_api_keys_for_user method of UserController.
    This test checks if API keys for a user can be listed successfully.
    """
    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the UserController with the mocked Prisma client
    controller = UserController(
        prisma=prisma_mock.return_value,
        supabase=None,
        supabase_admin=None,
        logger=logger
    )

    # Mock the ApiKeyService's get_api_keys_by_user method
    api_key_mock = MagicMock()
    api_key_mock.api_key_id = '123e4567-e89b-12d3-a456-426614174001'
    api_key_mock.expires_at = datetime.utcnow() + timedelta(days=30)
    api_key_mock.is_active = True
    api_key_mock.dict.return_value = {
        'api_key_id': api_key_mock.api_key_id,
        'expires_at': api_key_mock.expires_at.isoformat(),
        'is_active': api_key_mock.is_active
    }

    api_key_service_mock = AsyncMock()
    api_key_service_mock.get_api_keys_by_user.return_value = [api_key_mock]
    controller.api_key_service = api_key_service_mock

    # Call the list_api_keys_for_user method
    result = await controller.list_api_keys_for_user(user_id)

    # Assertions to verify the result
    assert result is not None
    assert len(result) == 1
    assert result[0]['api_key_id'] == '123e4567-e89b-12d3-a456-426614174001'
    assert result[0]['is_active'] is True

# Test for the create_api_key method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.user_controller.Prisma')
async def test_create_api_key(prisma_mock, user_id, logger):
    """
    Test the create_api_key method of UserController.
    This test checks if a new API key can be created for a user.
    """
    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the UserController with the mocked Prisma client
    controller = UserController(
        prisma=prisma_mock.return_value,
        supabase=None,
        supabase_admin=None,
        logger=logger
    )

    # Mock the ApiKeyService's create_api_key method
    api_key_mock = MagicMock()
    api_key_mock.api_key_id = '123e4567-e89b-12d3-a456-426614174001'
    raw_api_key = 'raw_api_key_value'
    expires_at = datetime.utcnow() + timedelta(days=30)

    api_key_service_mock = AsyncMock()
    api_key_service_mock.create_api_key.return_value = (api_key_mock, raw_api_key)
    controller.api_key_service = api_key_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Call the create_api_key method
    result = await controller.create_api_key(str(user_id))

    # Assertions to verify the result
    assert result['success'] is True
    assert result['api_key_id'] == api_key_mock.api_key_id
    assert result['raw_api_key'] == raw_api_key
    assert 'expires_at' in result

# Test for the revoke_api_key method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.user_controller.Prisma')
async def test_revoke_api_key(prisma_mock, user_id, logger):
    """
    Test the revoke_api_key method of UserController.
    This test checks if an API key can be revoked successfully.
    """
    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the UserController with the mocked Prisma client
    controller = UserController(
        prisma=prisma_mock.return_value,
        supabase=None,
        supabase_admin=None,
        logger=logger
    )

    # Mock the ApiKeyService's revoke_api_key method
    api_key_service_mock = AsyncMock()
    api_key_service_mock.revoke_api_key.return_value = True
    controller.api_key_service = api_key_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Call the revoke_api_key method
    api_key_id = UUID('123e4567-e89b-12d3-a456-426614174001')
    result = await controller.revoke_api_key(user_id, api_key_id)

    # Assertions to verify the result
    assert result is True

# Test for the delete_api_key method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.user_controller.Prisma')
async def test_delete_api_key(prisma_mock, user_id, logger):
    """
    Test the delete_api_key method of UserController.
    This test checks if an API key can be deleted successfully.
    """
    # Mock the Prisma client transaction context manager
    tx_mock = AsyncMock()
    prisma_mock.return_value.tx.return_value.__aenter__.return_value = tx_mock
    prisma_mock.return_value.tx.return_value.__aexit__.return_value = None

    # Instantiate the UserController with the mocked Prisma client
    controller = UserController(
        prisma=prisma_mock.return_value,
        supabase=None,
        supabase_admin=None,
        logger=logger
    )

    # Mock the ApiKeyService's delete_api_key method
    api_key_service_mock = AsyncMock()
    api_key_service_mock.delete_api_key.return_value = True
    controller.api_key_service = api_key_service_mock

    # Mock the AuditService's create_audit_log method
    audit_service_mock = AsyncMock()
    audit_service_mock.create_audit_log.return_value = True
    controller.audit_service = audit_service_mock

    # Call the delete_api_key method
    api_key_id = UUID('123e4567-e89b-12d3-a456-426614174001')
    result = await controller.delete_api_key(user_id, api_key_id)

    # Assertions to verify the result
    assert result is True

# Test for the get_user_profile method
@pytest.mark.asyncio
@patch('backend.app.features.core.controllers.user_controller.Prisma')
async def test_get_user_profile(prisma_mock, user_id, logger):
    """
    Test the get_user_profile method of UserController.
    This test checks if a user's profile can be retrieved successfully.
    """
    # Instantiate the UserController with the mocked Prisma client
    controller = UserController(
        prisma=prisma_mock.return_value,
        supabase=None,
        supabase_admin=None,
        logger=logger
    )

    # Mock the UserService's get_profile_by_user_id method
    mock_profile = MagicMock()
    mock_profile.auth_uid = str(user_id)
    mock_profile.username = 'test_user'
    mock_profile.email = 'test_user@example.com'

    user_service_mock = AsyncMock()
    user_service_mock.get_profile_by_user_id.return_value = mock_profile
    controller.user_service = user_service_mock

    # Call the get_user_profile method
    result = await controller.get_user_profile(str(user_id))

    # Assertions to verify the result
    assert result['success'] is True
    assert result['profile']['auth_uid'] == str(user_id)
    assert result['profile']['username'] == 'test_user'
    assert result['profile']['email'] == 'test_user@example.com'
