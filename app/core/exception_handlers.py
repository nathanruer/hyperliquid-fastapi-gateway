"""
Global exception handlers for FastAPI application.

This module provides centralized error handling for all application exceptions,
ensuring consistent error responses and proper logging.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.core.exceptions import (
    HyperliquidBotException,
    ExchangeNotConfiguredError,
    InvalidAddressError,
    TradingError,
    ConfigurationError,
    TelegramNotificationError
)
from app.core.logger import setup_logger

logger = setup_logger(__name__)


async def hyperliquid_bot_exception_handler(request: Request, exc: HyperliquidBotException) -> JSONResponse:
    """
    Handle custom Hyperliquid bot exceptions.
    
    Returns appropriate HTTP status codes based on exception type.
    """
    logger.error(f"HyperliquidBotException: {exc.message}", exc_info=True)
    
    # Determine status code based on exception type
    if isinstance(exc, ExchangeNotConfiguredError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(exc, (InvalidAddressError, TradingError)):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, ConfigurationError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exc, TelegramNotificationError):
        # Telegram errors shouldn't fail the request
        status_code = status.HTTP_200_OK
        logger.warning(f"Telegram notification failed but request succeeded: {exc.message}")
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": exc.message,
            "error_type": exc.__class__.__name__
        }
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    Returns detailed validation error information.
    """
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Erreur de validation des données",
            "errors": exc.errors()
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all other unhandled exceptions.
    
    This is the last resort handler for unexpected errors.
    """
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Erreur interne du serveur",
            "error": str(exc) if logger.level <= 10 else "Une erreur inattendue s'est produite"
        }
    )
