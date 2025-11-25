"""
FastAPI dependency injection functions.

This module contains shared dependencies for the API,
such as service instances, authentication, rate limiting, etc.
"""

from typing import Annotated
from fastapi import Depends, Request
from app.services.hyperliquid_service import HyperliquidService, hyperliquid_service
from app.core.middleware import verify_api_key


def get_hyperliquid_service() -> HyperliquidService:
    """
    Dependency injection for HyperliquidService.
    
    Returns:
        Global instance of HyperliquidService
    """
    return hyperliquid_service


# Type aliases for dependency injection
HyperliquidServiceDep = Annotated[HyperliquidService, Depends(get_hyperliquid_service)]
APIKeyDep = Annotated[str, Depends(verify_api_key)]
