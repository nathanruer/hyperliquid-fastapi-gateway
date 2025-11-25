import pytest
from app.core.exceptions import (
    HyperliquidBotException,
    ExchangeNotConfiguredError,
    InvalidAddressError,
    TradingError,
    ConfigurationError,
    TelegramNotificationError
)


def test_base_exception():
    """Test that base exception can be raised."""
    with pytest.raises(HyperliquidBotException):
        raise HyperliquidBotException("Test error")


def test_exchange_not_configured_error():
    """Test ExchangeNotConfiguredError."""
    error = ExchangeNotConfiguredError()
    assert "Exchange non configuré" in str(error)
    assert isinstance(error, HyperliquidBotException)


def test_exchange_not_configured_error_custom_message():
    """Test ExchangeNotConfiguredError with custom message."""
    custom_msg = "Custom error message"
    error = ExchangeNotConfiguredError(custom_msg)
    assert str(error) == custom_msg


def test_invalid_address_error():
    """Test InvalidAddressError."""
    address = "0xinvalid"
    error = InvalidAddressError(address)
    assert address in str(error)
    assert "invalide" in str(error).lower()


def test_invalid_address_error_with_reason():
    """Test InvalidAddressError with custom reason."""
    address = "0x123"
    reason = "Too short"
    error = InvalidAddressError(address, reason)
    assert address in str(error)
    assert reason in str(error)


def test_trading_error():
    """Test TradingError."""
    operation = "ouverture de position"
    details = "Insufficient balance"
    error = TradingError(operation, details)
    assert operation in str(error)
    assert details in str(error)


def test_configuration_error():
    """Test ConfigurationError."""
    config_key = "SECRET_KEY"
    reason = "Missing value"
    error = ConfigurationError(config_key, reason)
    assert config_key in str(error)
    assert reason in str(error)


def test_telegram_notification_error():
    """Test TelegramNotificationError."""
    reason = "Invalid bot token"
    error = TelegramNotificationError(reason)
    assert reason in str(error)
    assert "Telegram" in str(error)


def test_exception_inheritance():
    """Test that all custom exceptions inherit from base exception."""
    assert issubclass(ExchangeNotConfiguredError, HyperliquidBotException)
    assert issubclass(InvalidAddressError, HyperliquidBotException)
    assert issubclass(TradingError, HyperliquidBotException)
    assert issubclass(ConfigurationError, HyperliquidBotException)
    assert issubclass(TelegramNotificationError, HyperliquidBotException)
