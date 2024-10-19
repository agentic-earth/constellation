import pytest
from unittest.mock import Mock, AsyncMock
from prisma import Prisma
from uuid import UUID
from backend.app.features.core.services.user_service import UserService

@pytest.fixture
def mock_supabase_client():
    mock_client = Mock()
    mock_client.auth = AsyncMock()
    mock_client.auth.sign_up = AsyncMock()
    mock_client.auth.sign_in_with_password = AsyncMock()
    mock_client.auth.admin = AsyncMock()
    mock_client.auth.admin.delete_user = AsyncMock()
    return mock_client

@pytest.fixture
def user_service(mock_supabase_client):
    prisma_mock = Mock(spec=Prisma)
    return UserService(prisma_mock, mock_supabase_client)
import pytest
from uuid import UUID
from unittest.mock import AsyncMock, Mock

TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "securepassword123"
TEST_USERNAME = "testuser"
TEST_USER_ID = UUID("12345678-1234-5678-1234-567812345678")

@pytest.mark.asyncio
async def test_register_user_email_password(user_service, mock_supabase_client):
    mock_supabase_client.auth.sign_up.return_value.user = Mock(id=str(TEST_USER_ID))
    mock_supabase_client.auth.sign_up.return_value.session = Mock()
    user_service.prisma.profile.find_unique = AsyncMock(return_value=Mock(auth_uid=str(TEST_USER_ID)))

    result = await user_service.register_user_email_password(TEST_EMAIL, TEST_PASSWORD, TEST_USERNAME)
    
    assert result is not None
    assert result.auth_uid == str(TEST_USER_ID)
    mock_supabase_client.auth.sign_up.assert_called_once_with({
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "options": {"data": {"username": TEST_USERNAME}}
    })

@pytest.mark.asyncio
async def test_sign_in_user_email_password(user_service, mock_supabase_client):
    mock_session = Mock()
    mock_session.user.id = str(TEST_USER_ID)
    mock_supabase_client.auth.sign_in_with_password.return_value.session = mock_session

    result = await user_service.sign_in_user_email_password(TEST_EMAIL, TEST_PASSWORD)
    
    assert result is not None
    assert result["success"] is True
    assert result["session"] == mock_session
    mock_supabase_client.auth.sign_in_with_password.assert_called_once_with({
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })

@pytest.mark.asyncio
async def test_get_profile_by_user_id(user_service):
    mock_profile = Mock(auth_uid=str(TEST_USER_ID))
    user_service.prisma.profile.find_unique = AsyncMock(return_value=mock_profile)

    result = await user_service.get_profile_by_user_id(TEST_USER_ID)
    
    assert result is not None
    assert result.auth_uid == str(TEST_USER_ID)
    user_service.prisma.profile.find_unique.assert_called_once_with(where={"auth_uid": str(TEST_USER_ID)})

@pytest.mark.asyncio
async def test_update_profile(user_service):
    update_data = {"username": "newusername"}
    mock_profile = Mock(auth_uid=str(TEST_USER_ID))
    user_service.prisma.profile.update = AsyncMock(return_value=mock_profile)

    result = await user_service.update_profile(TEST_USER_ID, update_data)
    
    assert result is not None
    assert result.auth_uid == str(TEST_USER_ID)
    user_service.prisma.profile.update.assert_called_once_with(
        where={"auth_uid": str(TEST_USER_ID)},
        data=update_data
    )

@pytest.mark.asyncio
async def test_delete_user(user_service, mock_supabase_client):
    mock_supabase_client.auth.admin.delete_user.return_value = Mock(error=None)

    result = await user_service.delete_user(TEST_USER_ID)
    
    assert result is True
    mock_supabase_client.auth.admin.delete_user.assert_called_once_with(str(TEST_USER_ID))