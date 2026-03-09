import pytest
from unittest.mock import patch, MagicMock
import os
from dotenv import load_dotenv
from os.path import join, dirname, abspath

# --- Global Path Setup (CRITICAL FIX) ---
# Find the project root directory (two levels up from 'app/iLibrary/tests')
PROJECT_ROOT = abspath(join(dirname(__file__), '..', '..', '..'))

# --- Setup Environment for Testing (Reads .env file) ---
DOTENV_PATH = join(PROJECT_ROOT, '.env')
load_dotenv(DOTENV_PATH)

# Use os.environ directly, as load_dotenv has been called.
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SYSTEM = os.environ.get("DB_SYSTEM")
DB_DRIVER = os.environ.get("DB_DRIVER")
DB_LIB = os.environ.get("DB_LIB")
DB_REMPATH = os.environ.get("DB_REMPATH")
LOCAL_PATH = join(PROJECT_ROOT, 'app')


# --- Assuming the same environment setup as your previous snippet ---

@pytest.fixture
def mock_user_context():
    """
    Mocks the User class specifically.
    """
    mock_user_class = MagicMock()
    mock_user_instance = MagicMock()

    # Configure the mock instance to return a dummy user profile
    mock_user_instance.getSingleUserInformation.return_value = {
        "USERNAME": "ALBEER",
    }

    # Configure the context manager behavior
    mock_user_class.return_value.__enter__.return_value = mock_user_instance

    # Patch the 'User' class.
    # NOTE: Change 'your_module.User' to the actual import path
    with patch('iLibrary.User', mock_user_class):
        yield mock_user_class, mock_user_instance


def test_get_single_user_info_mapepire(mock_user_context):
    """
    Tests the getSingleUserInformation call with mapepire=True.
    """
    mock_user_class, user_instance = mock_user_context

    # Define test constants
    TEST_USER = DB_USER

    # --- The actual code execution ---
    # In your real code, this would be: with User(...) as lib:
    with mock_user_class(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=True) as lib:
        data = lib.getSingleUserInformation(username=TEST_USER)

    # --- Assertions ---

    # 1. Assert the constructor was called with the mapepire flag
    mock_user_class.assert_called_once_with(
        DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=True
    )

    # 2. Assert the specific method was called with the correct username
    user_instance.getSingleUserInformation.assert_called_once_with(username=TEST_USER)

    # 3. Assert the data returned matches our mock
    assert data["USERNAME"] == TEST_USER


def test_get_single_user_info_odbc(mock_user_context):
    """
    Tests initialization and call when Mapepire is DISABLED (ODBC mode).
    """
    mock_user_class, user_instance = mock_user_context
    TEST_USER = DB_USER

    # Pass mapepire=False here
    with mock_user_class(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=False) as lib:
        data = lib.getSingleUserInformation(username=TEST_USER)
        print(data)
    # FIX: Assert constructor received mapepire=False
    mock_user_class.assert_called_once_with(
        DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=False
    )

    user_instance.getSingleUserInformation.assert_called_once_with(username=TEST_USER)
    assert data["USERNAME"] == TEST_USER