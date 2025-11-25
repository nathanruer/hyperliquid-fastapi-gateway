"""
Custom exceptions for the Hyperliquid bot.

This module defines application-specific exceptions for better error handling
and more precise error messages.
"""


class HyperliquidBotException(Exception):
    """Base exception for all Hyperliquid bot errors."""
    pass


class ExchangeNotConfiguredError(HyperliquidBotException):
    """
    Raised when attempting to trade without proper exchange configuration.
    
    This typically means SECRET_KEY or ACCOUNT_ADDRESS is missing.
    """
    def __init__(self, message: str = "Exchange non configuré pour le trading. Vérifiez SECRET_KEY et ACCOUNT_ADDRESS."):
        self.message = message
        super().__init__(self.message)


class InvalidAddressError(HyperliquidBotException):
    """
    Raised when an Ethereum address is invalid.
    
    Valid addresses must:
    - Start with '0x'
    - Be 42 characters long (including '0x')
    - Contain only hexadecimal characters
    """
    def __init__(self, address: str, reason: str = "Format invalide"):
        self.address = address
        self.reason = reason
        self.message = f"Adresse Ethereum invalide '{address}': {reason}"
        super().__init__(self.message)


class TradingError(HyperliquidBotException):
    """
    Raised when a trading operation fails.
    
    This can include order placement failures, position closing errors, etc.
    """
    def __init__(self, operation: str, details: str):
        self.operation = operation
        self.details = details
        self.message = f"Erreur lors de {operation}: {details}"
        super().__init__(self.message)


class ConfigurationError(HyperliquidBotException):
    """
    Raised when configuration is invalid or incomplete.
    
    This includes missing required environment variables,
    invalid JSON format, etc.
    """
    def __init__(self, config_key: str, reason: str):
        self.config_key = config_key
        self.reason = reason
        self.message = f"Configuration invalide pour '{config_key}': {reason}"
        super().__init__(self.message)


class TelegramNotificationError(HyperliquidBotException):
    """
    Raised when sending a Telegram notification fails.
    
    This can be due to invalid bot token, chat ID, network issues, etc.
    """
    def __init__(self, reason: str):
        self.reason = reason
        self.message = f"Erreur d'envoi de notification Telegram: {reason}"
        super().__init__(self.message)
