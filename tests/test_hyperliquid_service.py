import pytest
from unittest.mock import Mock, patch
from app.services.hyperliquid_service import HyperliquidService
from app.core.exceptions import ExchangeNotConfiguredError, TradingError
from app.models.schemas import MarketOrderRequest, MarketCloseRequest


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch('app.services.hyperliquid_service.settings') as mock:
        mock.ACCOUNT_ADDRESS = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
        mock.SECRET_KEY = "test_secret_key"
        yield mock


@pytest.fixture
def mock_exchange():
    """Mock Exchange for testing."""
    with patch('app.services.hyperliquid_service.Exchange') as mock:
        yield mock


@pytest.fixture
def mock_info():
    """Mock Info client for testing."""
    with patch('app.services.hyperliquid_service.Info') as mock:
        yield mock


def test_service_initialization_without_credentials():
    """Test that service initializes without exchange if credentials missing."""
    with patch('app.services.hyperliquid_service.settings') as mock_settings:
        mock_settings.ACCOUNT_ADDRESS = ""
        mock_settings.SECRET_KEY = ""
        
        with patch('app.services.hyperliquid_service.Info'):
            service = HyperliquidService()
            assert service.exchange_instance is None
            assert service.account_address is None


def test_create_market_order_without_exchange():
    """Test that create_market_order raises error when exchange not configured."""
    with patch('app.services.hyperliquid_service.settings') as mock_settings:
        mock_settings.ACCOUNT_ADDRESS = ""
        mock_settings.SECRET_KEY = ""
        
        with patch('app.services.hyperliquid_service.Info'):
            service = HyperliquidService()
            order = MarketOrderRequest(coin="BTC", is_buy=True, size=0.01)
            
            with pytest.raises(ExchangeNotConfiguredError):
                service.create_market_order(order)


def test_close_market_position_without_exchange():
    """Test that close_market_position raises error when exchange not configured."""
    with patch('app.services.hyperliquid_service.settings') as mock_settings:
        mock_settings.ACCOUNT_ADDRESS = ""
        mock_settings.SECRET_KEY = ""
        
        with patch('app.services.hyperliquid_service.Info'):
            service = HyperliquidService()
            close_request = MarketCloseRequest(coin="BTC")
            
            with pytest.raises(ExchangeNotConfiguredError):
                service.close_market_position(close_request)


def test_get_user_state():
    """Test get_user_state calls info_client correctly."""
    with patch('app.services.hyperliquid_service.settings') as mock_settings:
        mock_settings.ACCOUNT_ADDRESS = ""
        mock_settings.SECRET_KEY = ""
        
        with patch('app.services.hyperliquid_service.Info') as mock_info_class:
            mock_info_instance = Mock()
            mock_info_class.return_value = mock_info_instance
            mock_info_instance.user_state.return_value = {"test": "data"}
            
            service = HyperliquidService()
            result = service.get_user_state("0xTest")
            
            mock_info_instance.user_state.assert_called_once_with("0xTest")
            assert result == {"test": "data"}
