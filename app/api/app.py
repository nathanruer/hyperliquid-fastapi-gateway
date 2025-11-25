from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.routers.v1.endpoints import trading, user_state, health
from app.api.routers import root
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.exceptions import HyperliquidBotException
from app.core.exception_handlers import (
    hyperliquid_bot_exception_handler,
    validation_error_handler,
    generic_exception_handler
)

logger = setup_logger(__name__)

limiter = Limiter(key_func=get_remote_address)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Hyperliquid Trading & State API",
        description="API pour récupérer l'état et interagir avec Hyperliquid",
        version="1.1.0"
    )

    app.state.limiter = limiter
    
    # Register exception handlers
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_exception_handler(HyperliquidBotException, hyperliquid_bot_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-API-Key"],
    )
    
    app.include_router(root.router)
    app.include_router(health.router, prefix="/v1", tags=["Health"])
    app.include_router(trading.router, prefix="/v1", tags=["Trading"])
    app.include_router(user_state.router, prefix="/v1", tags=["User State"])
    
    logger.info(f"✓ API v1.1.0 initialisée")

    return app
