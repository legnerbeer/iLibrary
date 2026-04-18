import pytest
from unittest.mock import patch, MagicMock
import os
from dotenv import load_dotenv
from os.path import join, dirname, abspath
import iLibrary

# --- Global Path Setup ---
# Find the project root directory (three levels up from 'app/iLibrary/tests')
PROJECT_ROOT = abspath(join(dirname(__file__), '..', '..', '..'))

# --- Setup Environment for Testing ---
DOTENV_PATH = join(PROJECT_ROOT, '.env')
load_dotenv(DOTENV_PATH)

# Use a fallback value "ALBEER" if the environment variable is missing
# This prevents the 'AssertionError: assert "ALBEER" == ""' in CI environments
DB_USER = os.environ.get("DB_USER", "ALBEER")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
DB_SYSTEM = os.environ.get("DB_SYSTEM", "localhost")
DB_DRIVER = os.environ.get("DB_DRIVER", "IBM i Access ODBC Driver")

@pytest.fixture
def mock_user_context():
    """
    Mocks the iLibrary.User class specifically.
    """
    mock_user_class = MagicMock()
    mock_user_instance = MagicMock()

    # Define a side effect to ensure the mock returns whatever username is requested
    # This makes the test resilient to changes in environment variables
    def dynamic_user_info(username):
        return {"USERNAME": username}

    mock_user_instance.getSingleUserInformation.side_effect = dynamic_user_info

    # Configure the context manager behavior (the 'with' statement)
    mock_user_class.return_value.__enter__.return_value = mock_user_instance

    # Patch the 'User' class inside the iLibrary package
    with patch('iLibrary.User', mock_user_class):
        yield mock_user_class, mock_user_instance


def test_get_single_user_info_mapepire(mock_user_context):
    """
    Tests the getSingleUserInformation call with mapepire=True.
    """
    mock_user_class, user_instance = mock_user_context
    TEST_USER = DB_USER

    # Execute the code under test
    with iLibrary.User(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=True) as lib:
        data = lib.getSingleUserInformation(username=TEST_USER)

    # --- Assertions ---
    # 1. Assert constructor received the correct arguments
    mock_user_class.assert_called_once_with(
        DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=True
    )

    # 2. Assert the method was called with the correct username
    user_instance.getSingleUserInformation.assert_called_once_with(username=TEST_USER)

    # 3. Assert the data returned matches the input (ALBEER == ALBEER)
    assert data["USERNAME"] == TEST_USER


def test_get_single_user_info_odbc(mock_user_context):
    """
    Tests initialization and call when Mapepire is DISABLED (ODBC mode).
    """
    mock_user_class, user_instance = mock_user_context
    TEST_USER = DB_USER

    # Execute with mapepire=False
    with iLibrary.User(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=False) as lib:
        data = lib.getSingleUserInformation(username=TEST_USER)

    # --- Assertions ---
    mock_user_class.assert_called_once_with(
        DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER, mapepire=False
    )

    user_instance.getSingleUserInformation.assert_called_once_with(username=TEST_USER)
    assert data["USERNAME"] == TEST_USER