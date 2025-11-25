import pytest
from unittest.mock import Mock, patch
from app.services.telegram_service import TelegramService


@pytest.fixture
def telegram_service():
    """Create TelegramService with mocked config."""
    with patch('app.services.telegram_service.settings') as mock_settings:
        mock_settings.TELEGRAM_BOT_TOKEN = "test_token_123"
        mock_settings.TELEGRAM_CHAT_ID = "test_chat_id_456"
        yield TelegramService()


@pytest.fixture
def telegram_service_no_config():
    """Create TelegramService without config."""
    with patch('app.services.telegram_service.settings') as mock_settings:
        mock_settings.TELEGRAM_BOT_TOKEN = ""
        mock_settings.TELEGRAM_CHAT_ID = ""
        yield TelegramService()


@pytest.fixture
def sample_fill():
    """Sample fill data for testing."""
    return {
        'coin': 'BTC',
        'px': '50000.5',
        'sz': '0.1',
        'side': 'B',  # Buy
        'closedPnl': '100.5'
    }


def test_telegram_service_initialization(telegram_service):
    """Test that TelegramService initializes correctly."""
    assert telegram_service.token == "test_token_123"
    assert telegram_service.chat_id == "test_chat_id_456"


def test_telegram_service_no_config_warning(telegram_service_no_config):
    """Test that missing config doesn't crash, just warns."""
    assert telegram_service_no_config.token == ""
    assert telegram_service_no_config.chat_id == ""


def test_format_fill_message_buy(telegram_service, sample_fill):
    """Test formatting a buy order message."""
    message = telegram_service._format_fill_message(sample_fill, "0xTest123")
    
    assert "ACHAT" in message or "Buy" in message
    assert "BTC" in message
    assert "50000.5" in message
    assert "0.1" in message
    assert "100.5" in message
    assert "0xTe" in message  # Shortened address


def test_format_fill_message_sell(telegram_service):
    """Test formatting a sell order message."""
    sell_fill = {
        'coin': 'ETH',
        'px': '3000',
        'sz': '1.5',
        'side': 'A',  # Ask/Sell
        'closedPnl': '-50.25'
    }
    
    message = telegram_service._format_fill_message(sell_fill, "0xAddress456")
    
    assert "VENTE" in message or "Sell" in message
    assert "ETH" in message
    assert "3000" in message
    assert "1.5" in message
    assert "-50.25" in message


def test_format_fill_message_unknown_side(telegram_service):
    """Test formatting message with unknown side."""
    unknown_fill = {
        'coin': 'ASTER',
        'px': '0.5',
        'sz': '100',
        'side': 'X',  # Unknown
        'closedPnl': '0'
    }
    
    message = telegram_service._format_fill_message(unknown_fill, "0xTest")
    
    assert "ASTER" in message
    assert "0.5" in message
    assert "100" in message


@patch('app.services.telegram_service.requests.post')
def test_send_message_success(mock_post, telegram_service, sample_fill):
    """Test successful message sending."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    
    telegram_service.send_trade_alert(sample_fill, "0xTest")
    
    assert mock_post.called
    call_args = mock_post.call_args
    
    assert "api.telegram.org" in call_args[0][0]
    assert "test_token_123" in call_args[0][0]
    
    payload = call_args[1]['json']
    assert payload['chat_id'] == "test_chat_id_456"
    assert payload['parse_mode'] == "HTML"
    assert 'BTC' in payload['text']


@patch('app.services.telegram_service.requests.post')
def test_send_message_api_error(mock_post, telegram_service, sample_fill):
    """Test handling of Telegram API error."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_post.return_value = mock_response
    
    telegram_service.send_trade_alert(sample_fill, "0xTest")
    
    assert mock_post.called


@patch('app.services.telegram_service.requests.post')
def test_send_message_network_error(mock_post, telegram_service, sample_fill):
    """Test handling of network error."""
    mock_post.side_effect = Exception("Network error")
    
    telegram_service.send_trade_alert(sample_fill, "0xTest")
    
    assert mock_post.called


def test_send_trade_alert_without_config(telegram_service_no_config, sample_fill):
    """Test that sending alert without config doesn't crash."""
    telegram_service_no_config.send_trade_alert(sample_fill, "0xTest")
