import pytest


@pytest.fixture
def valid_eth_address():
    """Return a valid Ethereum address for testing."""
    return "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"


@pytest.fixture
def invalid_eth_address():
    """Return an invalid Ethereum address for testing."""
    return "0xinvalid"


@pytest.fixture
def test_config():
    """Return test configuration dictionary."""
    return {
        "ACCOUNT_ADDRESS": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
        "SECRET_KEY": "test_secret_key_placeholder",
        "USERS_LISTENED": ["0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"],
        "TELEGRAM_BOT_TOKEN": "",
        "TELEGRAM_CHAT_ID": "",
        "API_HOST": "127.0.0.1",
        "API_PORT": 8000
    }
